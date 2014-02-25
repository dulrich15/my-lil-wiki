﻿from __future__ import division
from __future__ import unicode_literals

import os

# from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from config import pg_path
from utils import render_to_response

from models import *


def list_by_name(request):
    pg_walk = next(os.walk(pg_path))
    
    context = {
        'dirs': sorted(pg_walk[1]),
        'files': sorted(pg_walk[2]),
    }
    template = 'wiki/list_by_name.html'
    return render_to_response(request, template, context)


def show(request, pg='_'):
# do I really *need* a WikiRoot page?
    page = Page(pg)
    if pg == '_' and not page.content:
        return list_by_name(request)
        
    context = {
        'page' : page,
    }
    template = 'wiki/show.html'
    return render_to_response(request, template, context)

    
def edit(request, pg=''): 
# blank will create a *new* page --- how to edit WikiRoot page?
    if not request.user.is_staff:
        return redirect('wiki_root')
 
    page = Page(pg)

    context = {
        'page' : page,
    }
    template = 'wiki/edit.html'
    return render_to_response(request, template, context)
    
    
def post(request): 
    if request.user.is_staff and request.method == 'POST':
        pg = request.POST['pg']
        title = request.POST['title']
        title = re.sub('[\/]+$', '', title) # cut any trailing slashes off...
        title = re.sub('[^\w^\/]+', '', title) # poor man's validation attempt
        content = request.POST['content']
        content = content.replace('\r\n','\n')
        
        if 'cancel' not in request.POST:
            if '/' in title:
                check_path(title)

            page = Page(title)
            page.save(content)
            
            if title.lower() != pg.lower(): # case-sensitivity issue here?
            # then title was changed ... need to delete old file
                fp = os.path.join(pg_path, pg)
                if os.path.isfile(fp):
                    os.remove(fp)
                    
        if 'update' in request.POST:
            return redirect('wiki_edit', title)
        else:
            return redirect('wiki_show', title)

    # nothing should get here...
    return redirect('wiki_root')

    
def check_path(title):
    dirs = title.split('/')[:-1]
    if not os.path.isdir(os.path.join(pg_path, *dirs)):
        dir = pg_path
        for d in dirs:
            dir = os.path.join(dir, d)
            if not os.path.isdir(dir):
                if os.path.isfile(dir):
                    os.rename(dir, dir + '_')
                    os.mkdir(dir)
                    os.rename(dir + '_', os.path.join(dir, '_'))
                else:
                    os.mkdir(dir)

