from ast import Return
from typing import Annotated, List
from dagger.client.gen import BuildArg, Directory, File, ReturnType, Terminal
from typing_extensions import Doc
import dagger
from dagger import dag, function, object_type
import os

@object_type
class Basics:
   

    @function
    async def my_build_and_copy_2(
        self,
        src: Annotated[
            dagger.Directory,
            Doc("location of directory containing Dockerfile"),
        ],
        game_dir: Annotated[
            dagger.Directory,
            Doc("location of directory containing Game"),
        ],
        platform_build_container: Annotated[
            str,
            Doc("Which platform the build container is running on (x86_64 or arm64) "),
        ] = "arm64",
        platform: Annotated[
            str,
            Doc("Target platform for export (macos or linux or windows)"),
        ] = "macOS",
        addons: Annotated[
            str,
            Doc("Target platform for export (macos or linux or windows)"),
        ] = "NONE"
    ) -> dagger.File:
        """Build and export Godot project for specified platform from existing Dockerfile"""

        # Validate platform parameter
        platform_lower = platform.lower()
        if platform_lower not in ["macos", "linux", "windows"]:
            raise ValueError("Platform must be 'macos', 'windows' or 'Linux'")

        if platform_build_container == "x86_64":
            my_build_args: List[BuildArg] = [
                # BuildArg("GODOT_VERSION", "4.4.1"),
                BuildArg("GODOT_VERSION", "4.4"),
                BuildArg("GODOT_PLATFORM", "linux.x86_64"),    
                BuildArg("GODOT_ZIP_PLATFORM", "linux_x86_64"),
            ] 
        if platform_build_container == "arm64":
            my_build_args: List[BuildArg] = [
                # BuildArg("GODOT_VERSION", "4.4.1"),
                BuildArg("GODOT_VERSION", "4.4"),
                BuildArg("GODOT_PLATFORM", "linux.arm64"),
                BuildArg("GODOT_ZIP_PLATFORM", "linux_arm64"),
            ] 
                
        # Define export parameters
        # export_name = game_dir
        export_dir = f"/export_build/{platform_lower}"  # /build/macos or /build/linux
        export_path = f"{export_dir}/MYGAME.zip"
        
        if platform_lower == "macos":
            platform_name = "macOS"
        elif platform_lower == "windows":
            platform_name = "Windows Desktop"
        elif platform_lower == "linux":
            platform_name = "Linux"
        else:
            raise Exception(f"Bad Platform Name {platform_name}")

        #
        # BUILD CONTAINER FROM DOCKERFILE
        #
        container = src.docker_build(build_args=my_build_args)
        

        # Mount the filtered game directory
        container = (container
                        .with_mounted_directory("/GAMEDIR", game_dir))
        
        container = (
            container
            .with_env_variable("GODOT_VERSION", "4.4")
            .with_exec(["mkdir", "-p", export_dir])  # Create build/<platform> directory
            .with_workdir("/GAMEDIR")  # Set working directory to Godot project
        )

        await container.stdout()  # This forces the container to execute

        #
        # Install Addons
        #
        if addons == "NONE":
            container = container.with_exec(["echo", "----- Skipping Addons ----"])    
        elif addons == "NORMAL":
            container = (
                container
                .with_exec(["apt-get", "update"])
                .with_exec(["apt-get", "install", "-y", "wget", "unzip", "git"])
                
            )
            # # Use our install_addons function
            container = await self.install_addons(container, "/GAMEDIR")
        

        godot_command = f"godot --headless --verbose --export-release {platform_name} {export_path}"
        container = container.with_exec(["echo", f"=== Running command: {godot_command}"])
        #
        # BUILD GAME WITH GODOT
        #
        # Log the Godot command
        godot_command = f"godot --headless --verbose --export-release {platform_name} {export_path}"
        print(f"=== Running command: {godot_command}")

        # Run Godot export command, ignoring exit code 1
        container = container.with_exec(
            args=[
                "godot",
                "--headless",
                "--verbose",
                "--export-release",
                platform_name,
                export_path
            ],
            expect=ReturnType.ANY
        )
        await container.stdout()  # This forces the container to execute
        print(f"=== Godot exit code from build was:{container.exit_code} ")
        
        

        #
        # VERIFY AND RETURN FILE
        #
        try:
            # Get the exported file - this will throw an error if it doesn't exist
            exported_file = container.file(export_path)
            
            # Verify the file exists by checking its size (this forces evaluation)
            file_size = await exported_file.size()
            print(f"Export successful: {export_path} created with size {file_size} bytes")
            
            return exported_file
            
        except Exception as e:
            # If file doesn't exist, list directory contents for debugging
            print(f"=== Export failed: {e}") 
            raise Exception(f"Export failed: {export_path} was not created")



    @function
    async def install_addons(
        self,
        container: dagger.Container,
        addons_root_path: Annotated[
            str,
            Doc("Root path where addons folder should be located (e.g., '/game1')"),
        ] = "/game1"
        ) -> dagger.Container:
        """Install addons from various sources into the addons directory"""
        
        # Define the list of items to install (hardcoded for now)
        install_items = [
            {
                "type": "zip_url",
                "url": "https://github.com/utopia-rise/fmod-gdextension/releases/download/5.0.6-4.4.0/addons.zip",
                "folder_inside": "fmod"
            },
            {
                "type": "git_repo",
                "repo_url": "https://github.com/expressobits/inventory-system",
                # "branch": "addon-2.9.1",
                "branch": "addon-2.6.3",
                "source_path": "./addons/inventory-system"
            },
            {
                "type": "git_repo",
                "repo_url": "https://github.com/majikayogames/SimpleDungeons",
                "branch": "main",
                "source_path": "./addons/SimpleDungeons"
            }
        ]
        
        # Ensure addons directory exists
        addons_path = f"{addons_root_path}/addons"
        container = container.with_exec(["rm", "-rf", addons_path])
        container = container.with_exec(["mkdir", "-p", addons_path])
        container = container.with_exec(["ls", "-la", addons_path])
        
        # Process each install item
        for item in install_items:
            print(f"Processing item: {item}")
            
            if item["type"] == "zip_url":
                container = container.with_exec(["echo", f"------- addon: {item['type']} -- {item['folder_inside']}"])
                container = await self._install_from_zip_url(container, item, addons_path)
            elif item["type"] == "git_repo":
                container = container.with_exec(["echo", f"------- addon: {item['type']} -- {item['source_path']}"])
                container = await self._install_from_git_repo(container, item, addons_path)
            else:
                print(f"Unknown item type: {item['type']}")
        
        # await container.terminal()
        return container

    async def _install_from_zip_url(
        self,
        container: dagger.Container,
        item: dict,
        addons_path: str
    ) -> dagger.Container:
        """Install addon from a zip URL"""
        
        url = item["url"]
        folder_inside = item["folder_inside"]
        
        print(f"Installing from zip URL: {url}")
        print(f"Looking for folder: {folder_inside}")
        
        # Download and extract the zip file
        temp_zip = "/tmp/download.zip"
        temp_extract = "/tmp/extract"
        
        container = (
            container
            .with_exec(["mkdir", "-p", temp_extract])
            .with_exec(["wget", "-O", temp_zip, url])
            .with_exec(["unzip", "-q", temp_zip, "-d", temp_extract])
        )
        
        # Find and copy the specific folder
        source_folder = f"{temp_extract}/{folder_inside}"
        
        # Check if the folder exists and copy it
        container = (
            container
            .with_exec(["test", "-d", source_folder])  # Verify folder exists
            .with_exec(["cp", "-r", source_folder, "addons"])
            .with_exec(["ls", "-la", "addons"])
            .with_exec(["rm", "-rf", temp_zip, temp_extract])  # Cleanup
        )
        
        print(f"Successfully installed {folder_inside} from zip")
        return container

    async def _install_from_git_repo(
        self,
        container: dagger.Container,
        item: dict,
        addons_path: str
    ) -> dagger.Container:
        """Install addon from a git repository"""
        
        repo_url = item["repo_url"]
        branch = item["branch"]
        source_path = item["source_path"]
        
        print(f"Installing from git repo: {repo_url}")
        print(f"Branch: {branch}")
        print(f"Source path: {source_path}")
        
        # Clone the repository
        temp_repo = "/tmp/repo"
        
        container = (
            container
            .with_exec(["rm", "-rf", temp_repo])  # Clean up any existing temp repo
            .with_exec(["git", "clone", "--branch", branch, "--single-branch", repo_url, temp_repo])
        )
        
        # Extract addon name from source path (last part after /)
        addon_name = source_path.split('/')[-1]
        source_full_path = f"{temp_repo}/{source_path.lstrip('./')}"
        
        # Copy the addon folder
        container = (
            container
            .with_exec(["test", "-d", source_full_path])  # Verify source exists
            .with_exec(["cp", "-r", source_full_path, "addons"])
            .with_exec(["ls", "-la", "addons"])
            .with_exec(["rm", "-rf", temp_repo])  # Cleanup
        )
        
        print(f"Successfully installed {addon_name} from git repo")
        return container
    
