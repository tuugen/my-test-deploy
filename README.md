# introduction

Dagger + Omnibuilder examples in godot


# Running

### Omnibuilder

Use CI to build off omnibuilder image


### Dagger

To build projects locally w/ Dagger

```bash
# mac
dagger --verbose call my-build-and-copy-2 \
        --platform_build_container=arm64 \
        --platform=macos \
        --game_dir=../test_game1 \
        --src=../omnibuild \
        --addons=NORMAL \
        export --path=./my-export22.zip

dagger --verbose call my-build-and-copy-2 \
        --platform_build_container=arm64 \
        --platform=macos \
        --game_dir=../test_project \
        --src=../omnibuild \
        export --path=./my-export22.zip
```