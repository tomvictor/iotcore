//go:build mage

package main

import (
	"fmt"
	"github.com/magefile/mage/sh"
)

const GoBinaryName = "goiotbackend"

func packageName() string {
	//TODO: suffix platform
	return GoBinaryName
}

// Bootstrap project
func Bootstrap() {
	fmt.Println("Bootstrapping...")
}

func BuildGo() error {

	sh.RunV("pwd")

	if err := sh.RunV("go", "build", "-o", packageName()); err != nil {
		return err
	}

	if err := sh.RunV("mv", packageName(), "djangoiot"); err != nil {
		return err
	}

	fmt.Println("Go build done!")

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

	return Run()
}

// Run development django project
func Run() error {
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

func Release() error {
	return sh.RunV("twine", "upload", "dist/*")
}
