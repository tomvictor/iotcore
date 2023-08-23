//go:build mage

package main

import (
    "github.com/magefile/mage/sh"
    "fmt"
    "os"
)

// Bootstrap project
func Bootstrap(){
    fmt.Println("Bootstrapping...")
}

func BuildGo() error {
    os.Chdir("djangoiot")
	defer os.Chdir("..")

	sh.RunV("pwd")

    if err := sh.Run("go", "build", "iot.go"); err != nil {
        return err
    }

    fmt.Println("Gobuild done!")

    return nil
}


// Build djangoiot
func Build() error {
    if err := Clean(); err != nil {
        return err
    }
    fmt.Println("Building...")

    BuildGo()

    if err := sh.Run("python3", "-m", "build"); err != nil {
        return err
    }

    fmt.Println("Build finished!")
    return nil
}

// Clean, Build and Install dev version
func Dev() error {
    if err := Build(); err != nil {
        return err
    }

    fmt.Println("Install package!")

    // TODO: read version from file
    if err := sh.Run("pip", "install", "dist/dev-0.0.4.tar.gz"); err != nil {
        return err
    }

    fmt.Println("Package installed!")

    fmt.Println("Run development project..")

    return sh.RunV("python", "develop/manage.py", "runserver")
}

// Clean the builds
func Clean() error {
    fmt.Println("Cleaning...")

    if err := sh.Run("rm", "-rf", "build"); err != nil {
        return err
    }

    if err := sh.Run("rm", "-rf", "dist"); err != nil {
        return err
    }

    if err := sh.Run("rm", "-rf", "djangoiot.egg-info"); err != nil {
        return err
    }

    if err := sh.Run("rm", "-rf", "dev.egg-info"); err != nil {
        return err
    }

    if err := sh.Run("rm", "-rf", ".pytest_cache"); err != nil {
        return err
    }

    if err := sh.Run("rm", "-rf", "coverage"); err != nil {
        return err
    }

    fmt.Println("Cleaning Finished!")

    return nil
}

