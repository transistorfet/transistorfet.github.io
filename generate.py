
import re
import os
import json
import os.path
import argparse
import markdown
import subprocess


local_repos = "/media/home/git"
cannonical_root = 'https://jabberwocky.ca'
github_link_fmt = 'https://github.com/transistorfet/{}'
github_git_fmt = 'git@github.com:transistorfet/{}'

input_dir = "_input"
repos_dir = "_repos"
output_dir = "."


def load_projects(filename):
    with open(filename, 'r') as f:
        projects = json.load(f)
    return projects


def fetch_project(name, repo):
    if not os.path.exists(name):
        res = subprocess.run("git clone --no-checkout {}".format(repo), shell=True)
    else:
        res = subprocess.run("(cd {} && git fetch)".format(name), shell=True)

    if res.returncode != 0:
        print("Unable to fetch {} via {}".format(name, repo))
        return

    subprocess.run("(cd {} && git checkout origin/HEAD -- README.md)".format(name), shell=True)
    subprocess.run("(cd {} && git checkout origin/HEAD -- images)".format(name), shell=True)
    subprocess.run("(cd {} && git checkout origin/HEAD -- docs/posts)".format(name), shell=True)


def fetch_all_projects(projects):
    os.makedirs(repos_dir, exist_ok=True)
    os.chdir(repos_dir)

    for project in projects:
        print(project['name'])
        if 'repo' in project and project['repo']:
            source = project['repo'] if '://' in project['repo'] else project['repo'] if project['repo'].startswith('/') else os.path.join(local_repos, project['repo'])
            fetch_project(project['name'], source)

    os.chdir(''.join([ '..' for d in repos_dir.split('/') if d ]))


def copy_images(projects):
    for project in projects:
        print(project['name'])
        image_dirs = find_source_files(project['name'], 'images')
        if image_dirs:
            for images in image_dirs:
                subprocess.run("cp -R {} {}".format(images, os.path.join(output_dir, 'projects', project['name']) + '/'), shell=True)


def copy_post_images(post_dir):
    image_dir = os.path.join(post_dir, 'images')
    if os.path.exists(image_dir):
        subprocess.run("cp -R {} {}".format(image_dir, os.path.join(output_dir, 'posts') + '/'), shell=True)


def find_source_files(project, filename):
    paths = []
    path = os.path.join(input_dir, project, filename)
    if os.path.exists(path):
        paths.append(path)
    path = os.path.join(repos_dir, project, filename)
    if os.path.exists(path):
        paths.append(path)
    return paths


def get_markdown_files(dirname):
    if not os.path.exists(dirname):
        return []
    copy_post_images(dirname)
    return [ os.path.join(dirname, name) for name in os.listdir(dirname) if name.endswith('.md') ]


def collect_posts(projects):
    files = get_markdown_files(os.path.join(input_dir, 'posts'))
    for project in projects:
        files.extend(get_markdown_files(os.path.join(repos_dir, project['name'], 'docs', 'posts')))

    posts = []
    for filename in files:
        title = ""
        for line in load_file(filename).splitlines():
            if line.startswith("==="):
                break
            title = line
        dest = os.path.splitext(os.path.basename(filename))[0] + '.html'
        posts.append({ 'src': filename, 'dest': dest, 'title': title })
    posts.sort(key=lambda a: a['dest'])
    return posts


def load_file(filename):
    with open(filename, 'r') as f:
        return f.read()


def convert_markdown(filename):
    with open(filename, 'r') as f:
        text = f.read()
        html = markdown.markdown(text, extensions=['extra', 'codehilite'], extension_configs={ 'codehilite': { 'guess_lang': False } })
    return html


class Template (object):
    def __init__(self, filename, projects, posts):
        self.projects = projects
        self.posts = posts

        with open(filename, 'r') as f:
            self.template = f.read()

    def generate_sidebar(self, data):
        html = ''
        if data.get('project_github'):
            html += '<a href="#download">Get the Source</a><hr>\n'

        for project in self.projects:
            html += '<a href="{}">{}</a><br>\n'.format(os.path.join(data['rootdir'], 'projects', project['name']) + '/', project['title'])
        if self.posts and len(self.posts) > 0:
            html += '<hr>\n'
            html += '<h3>Posts</h3>\n'
            html += self.generate_posts_list(data)
        return html

    def generate_posts_list(self, data):
        html = '<ul>'
        for post in self.posts:
            html += '<li><a href="{}">{}</a></li>\n'.format(os.path.join(data['rootdir'], 'posts', post['dest']), post['title'])
        html += '</ul>'
        return html

    def generate_main_page(self, filename, data):
        html = load_file(filename)
        if self.posts and len(self.posts) > 0:
            html += '<h2>Posts</h2>\n'
            html += self.generate_posts_list(data)
        return html

    def generate_project_page(self, readme, data):
        html = convert_markdown(readme)
        if data.get('project_github'):
            html += '<hr>\n<a name="download"></a>\n<h3>Get the Source</h3>\n'
            html += '<a href="{0}">{0}</a><br><br>\n'.format(data['project_github'] if data['project_github'] != 'default' else github_link_fmt.format(data['project_name']))
            html += 'Or clone with:<pre><code>git clone {0}</code></pre>\n'.format(github_git_fmt.format(data['project_name']))
        return html

    def render_template(self, filename, html, data):
        data['cannonical_root'] = cannonical_root
        data['cannonical_link'] = os.path.join(cannonical_root, data['link'])

        fullpath = os.path.join(output_dir, filename)
        os.makedirs(os.path.dirname(fullpath), exist_ok=True)
        with open(fullpath, 'w') as f:
            data['sidebar'] = self.generate_sidebar(data)
            data['content'] = html
            f.write(self.template.format(**data))


def generate_site(projects, posts):
    os.makedirs(output_dir, exist_ok=True)
    template = Template(os.path.join(input_dir, 'index.template.html'), projects, posts)

    # Generate the main page index
    index = os.path.join(input_dir, 'index.html')
    if os.path.exists(index):
        data = dict(rootdir='.', link='', title='Projects')
        html = template.generate_main_page(index, data)
        template.render_template('index.html', html, data)

    # Generate each project readme page
    for project in projects:
        print(project['name'])

        # Generate project file from README markdown
        readme = find_source_files(project['name'], 'README.md')
        if readme:
            link = os.path.join('projects', project['name'])
            data = dict(rootdir='../..', link=link + '/', title=project['title'], project_name=project['name'], project_github=project['github'])
            template.render_template(os.path.join(link, 'index.html'), template.generate_project_page(readme[0], data), data)

    # Generate each post page
    for post in posts:
        link = os.path.join('posts', post['dest'])
        data = dict(rootdir='..', link=link, title=post['title'])
        template.render_template(link, convert_markdown(post['src']), data)


def main():
    parser = argparse.ArgumentParser(prog='generate', formatter_class=argparse.ArgumentDefaultsHelpFormatter, description='Fetch and generate website html from markdown')
    parser.add_argument('-F', '--no-fetch', action='store_true', help="Do not fetch repository data before generating")
    parser.add_argument('-G', '--no-generate', action='store_true', help="Do not generate the html")
    parser.add_argument('-C', '--no-copy', action='store_true', help="Do not copy images to the output directory")
    args = parser.parse_args()

    projects = load_projects('projects.json')

    if not args.no_fetch:
        fetch_all_projects(projects)
        if not args.no_copy:
            copy_images(projects)

    posts = collect_posts(projects)
    if not args.no_generate:
        generate_site(projects, posts)


if __name__ == '__main__':
    main()

