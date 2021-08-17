
import re
import os
import json
import os.path
import argparse
import markdown
import subprocess


local_repos = "/media/home/git"
repo_link_fmt = 'http://jabberwocky.ca/git/{}.git'
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
    subprocess.run("(cd {} && git checkout origin/HEAD -- docs/articles)".format(name), shell=True)


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


def get_markdown_files(dirname):
    if not os.path.exists(dirname):
        return []
    return [ os.path.join(dirname, name) for name in os.listdir(dirname) if name.endswith('.md') ]


def collect_articles(projects):
    files = get_markdown_files(os.path.join(input_dir, 'articles'))
    for project in projects:
        files.extend(get_markdown_files(os.path.join(repos_dir, project['name'], 'docs', 'articles')))

    articles = []
    for filename in files:
        title = ""
        for line in load_file(filename).splitlines():
            if line.startswith("==="):
                break
            title = line
        dest = os.path.splitext(os.path.basename(filename))[0] + '.html'
        articles.append({ 'src': filename, 'dest': dest, 'title': title })
    articles.sort(key=lambda a: a['dest'])
    return articles


def load_file(filename):
    with open(filename, 'r') as f:
        return f.read()


def convert_markdown(filename):
    with open(filename, 'r') as f:
        text = f.read()
        html = markdown.markdown(text, extensions=['extra'])
    return html


def make_output_path(*args):
    path = os.path.join(output_dir, *args[:-1])
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, args[-1])


class Template (object):
    def __init__(self, filename, projects, articles):
        self.projects = projects
        self.articles = articles

        with open(filename, 'r') as f:
            data = f.read()

        (header, remain) = re.split(r'[ \t]*\{% sidebar %\}[ \t]*\n', data, 1)
        (middle, footer) = re.split(r'[ \t]*\{% content %\}[ \t]*\n', remain, 1)

        self.header = header
        self.middle = middle
        self.footer = footer

    def generate_sidebar(self, data):
        html = ''
        if data.get('project_github'):
            html += '<a href="#download">Get the Source</a><hr>\n'

        for project in self.projects:
            html += '<a href="{}">{}</a><br>\n'.format(os.path.join(data['rootdir'], 'projects', project['name']), project['title'])
        if self.articles and len(self.articles) > 0:
            html += '<hr>\n'
            html += '<h3>Articles</h3>\n'
            html += self.generate_articles_list(data)
        return html

    def generate_articles_list(self, data):
        html = '<ul>'
        for article in self.articles:
            html += '<li><a href="{}">{}</a></li>\n'.format(os.path.join(data['rootdir'], 'articles', article['dest']), article['title'])
        html += '</ul>'
        return html

    def generate_download(self, name, github):
        html = '<hr>\n<a name="download"></a>\n<h3>Get the Source</h3>\n'
        html += '<a href="{0}">{0}</a><br><br>\n'.format(github if github != 'default' else github_link_fmt.format(name))
        html += 'Or clone with:<pre><code>git clone {0}</code></pre>\n'.format(github_git_fmt.format(name))
        return html

    def generate_project_index(self, filename, data):
        html = load_file(filename)
        if self.articles and len(self.articles) > 0:
            html += '<h2>Articles</h2>\n'
            html += self.generate_articles_list(data)
        return html

    def render_template(self, filename, html, data):
        with open(filename, 'w') as f:
            f.write(self.header.format(**data))
            f.write(self.generate_sidebar(data))
            f.write(self.middle.format(**data))
            f.write(html)
            if data.get('project_github'):
                f.write(self.generate_download(data['project_name'], data['project_github']))
            f.write(self.footer.format(**data))


def generate_site(projects, articles):
    os.makedirs(output_dir, exist_ok=True)
    template = Template(os.path.join(input_dir, 'index.template.html'), projects, articles)

    # Generate the project index
    index = os.path.join(input_dir, 'index.html')
    if os.path.exists(index):
        html = template.generate_project_index(index, dict(rootdir='.'))
        template.render_template(os.path.join(output_dir, 'index.html'), html, dict(rootdir='.', title='Projects'))

    for project in projects:
        print(project['name'])

        # Generate project file from README markdown
        readme = find_source_files(project['name'], 'README.md')
        if readme:
            destpath = make_output_path('projects', project['name'], 'index.html')
            data = dict(rootdir='../..', title=project['title'], project_name=project['name'], project_github=project['github'])
            template.render_template(destpath, convert_markdown(readme[0]), data)

    for article in articles:
        data = dict(rootdir='..', title=article['title'])
        template.render_template(os.path.join(output_dir, 'articles', article['dest']), convert_markdown(article['src']), data)


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

    articles = collect_articles(projects)
    if not args.no_generate:
        generate_site(projects, articles)


if __name__ == '__main__':
    main()

