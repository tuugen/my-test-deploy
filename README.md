# introduction

dagger to build omnibuild as container, then use it to build project with addons

```
step1: build omnibuild Dockerfile


step2: mimic github actions in dagger file

```


# Running

```bash
dagger --verbose call my-build-and-copy-2 \
        --platform_build_container=arm64 \
        --platform=macos \
        --game_dir=../test_project \
        --src=../omnibuild \
        export --path=./my-export22.zip
```