
import re
import os
import json
import os.path
import argparse
import markdown
import subprocess


local_repos = "/media/home/git"
repo_link_fmt = 'http://jabberwocky.ca/git/{}.git'
gitweb_link_fmt = 'http://jabberwocky.ca/gitweb/?p={}.git'
github_link_fmt = 'https://github.com/transistorfet/{}'

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


def find_source_files(project, filename):
    paths = []
    path = os.path.join(input_dir, project, filename)
    if os.path.exists(path):
        paths.append(path)
    path = os.path.join(repos_dir, project, filename)
    if os.path.exists(path):
        paths.append(path)
    return paths


def load_file(filename):
    with open(filename, 'r') as f:
        return f.read()


def convert_markdown(filename):
    with open(filename, 'r') as f:
        text = f.read()
        html = markdown.markdown(text, extensions=['extra'])
    return html


class Template (object):
    def __init__(self, filename, projects):
        self.projects = projects

        with open(filename, 'r') as f:
            data = f.read()

        (header, remain) = re.split(r'[ \t]*\{% sidebar %\}[ \t]*\n', data, 1)
        (middle, footer) = re.split(r'[ \t]*\{% content %\}[ \t]*\n', remain, 1)

        self.header = header
        self.middle = middle
        self.footer = footer

    def generate_sidebar(self, project, rootdir):
        html = ''
        if project:
            html += '<a href="#download">Get the Source</a><hr>'

        for project in self.projects:
            html += '<a href="{}">{}</a><br>\n'.format(os.path.join(rootdir, 'projects', project['name']), project['title'])
        return html

    def generate_download(self, project):
        html = '<hr>\n<a name="download"></a><h3>Get the Source</h3>'

        if 'github' in project and project['github']:
            html += '<a href="{0}">{0}</a><br>\n'.format(project['github'] if project['github'] != 'default' else github_link_fmt.format(project['name']))

        html += '<a href="{0}">{0}</a><br>\n'.format(gitweb_link_fmt.format(project['name']))

        if 'repo' in project and project['repo']:
            link = project['repo'] if '://' in project['repo'] else repo_link_fmt.format(project['name'])
            html += 'Or clone with:<pre><code>git clone {0}</code></pre>\n'.format(link)
        return html

    def render_template(self, filename, html, project=None):
        rootdir = '.' if not project else '../..'
        data = { 'rootdir': rootdir }

        with open(filename, 'w') as f:
            f.write(self.header.format(**data))
            f.write(self.generate_sidebar(project, rootdir))
            f.write(self.middle.format(**data))
            f.write(html)
            if project:
                f.write(self.generate_download(project))
            f.write(self.footer.format(**data))


def generate_site(projects):
    os.makedirs(output_dir, exist_ok=True)
    template = Template(os.path.join(input_dir, 'index.template.html'), projects)

    # Generate the project index
    index = os.path.join(input_dir, 'index.html')
    if os.path.exists(index):
        template.render_template(os.path.join(output_dir, 'index.html'), load_file(index))

    for project in projects:
        print(project['name'])
        project_output_dir = os.path.join(output_dir, 'projects', project['name'])
        os.makedirs(project_output_dir, exist_ok=True)

        # Generate project file from README markdown
        readme = find_source_files(project['name'], 'README.md')
        if readme:
            template.render_template(os.path.join(project_output_dir, 'index.html'), convert_markdown(readme[0]), project=project)


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

    if not args.no_generate:
        generate_site(projects)


if __name__ == '__main__':
    main()

