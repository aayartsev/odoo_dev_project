class AbstractCreateProjectEnvironment():

    def handle_git_link(self):
        NotImplementedError(
                f"""Define handle_git_link in {self.__class__.__name__}""")

    def map_folders(self):
        NotImplementedError(
                f"""Define map_folders in {self.__class__.__name__}""")
    
    def generate_dockerfile(self):
        NotImplementedError(
                f"""Define generate_dockerfile in {self.__class__.__name__}""")
    
    def generate_config_file(self):
        NotImplementedError(
                f"""Define generate_config_file in {self.__class__.__name__}""")
    
    def generate_docker_compose_file(self):
        NotImplementedError(
                f"""Define generate_docker_compose_file in {self.__class__.__name__}""")
    
    def checkout_dependencies(self):
        NotImplementedError(
                f"""Define checkout_dependencies in {self.__class__.__name__}""")
    
    def update_links(self):
        NotImplementedError(
                f"""Define update_links in {self.__class__.__name__}""")
    
    def update_vscode_debugger_launcher(self):
        NotImplementedError(
                f"""Define update_vscode_debugger_launcher in {self.__class__.__name__}""")
    
    def clone_odoo(self):
        NotImplementedError(
                f"""Define clone_odoo in {self.__class__.__name__}""")
    
    def build_image(self):
        NotImplementedError(
                f"""Define build_image in {self.__class__.__name__}""")