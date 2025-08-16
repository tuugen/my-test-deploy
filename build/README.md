# introduction

dagger build files,
TODO, will need to build godot_server images 
for when DM runs headless on linux server,
godot_server distributions are optoimized 

```
dagger -c 'mount-godot-directory game1 | terminal'

dagger -c 'build .'


dagger call build --dockerio_username=DOCKER_USERNAME \
`                 --dockerio_password=DOCKER_PASSWORD \
`                 --src=.

# VRAM Compression in project settings ...
# both checkboxes need to be checked
#
# MACOS: DISABLE CODESIGNING
#
# bulding....


# mac
godot --headless --verbose --export-release macOS /build/mac/game1.zip

HANGING ISSUE when project has blender assets....
https://github.com/godotengine/godot/issues/100122


#linux
1 thing minor
sudo apt install fontconfig

godot --headless --verbose --export-release macOS ./game1.zip
godot --headless --verbose --export-release Linux ./game1.zip
godot --headless --verbose --export-release Linux ./game1-no-audio.zip
godot --headless --verbose --export-pack Linux /build/linux/game2.zip

# building - game1
dagger --verbose call my-build-and-copy-2 --platform_build_container=arm64 \
       --platform=macos --game_dir=game1 --src=. export --path=./my-export22.zip

# building - my-nakama
r


# godot-ci-dagger -- from other project
▪dagger --verbose call build-and-process --platform_build_container=arm64 \
        --platform=macos --game_dir=../my-nakama-csharp \
        --src=.
```

# TODO:
// TODO: figur eout addons
https://github.com/chickensoft-games/GodotEnv
or just github clone?
or this? immature.. but nice
https://github.com/nilsiker/godam



## manual docker

```bash
docker build -t game1 .

# build for linux arm64 (runs on mac)?
docker build --build-arg GODOT_VERSION="4.4.1" \
             --build-arg GODOT_PLATFORM="linux.arm64" \
             --build-arg GODOT_ZIP_PLATFORM="linux_arm64" \
              -t d3509-linux-arm64-base .

docker run -it --platform=linux/arm64 d3509-linux-arm64-base bash


# build for mac
docker build --build-arg GODOT_VERSION="4.4.1" \
             --build-arg GODOT_PLATFORM="macos.universal" \
             --build-arg GODOT_ZIP_PLATFORM="macos.universal" \
              -t d3509-mac-base .
```