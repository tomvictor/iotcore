//go:build mage
// +build mage

package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"os"

	"github.com/magefile/mage/sh"
)

type Project struct {
	Version       string `json:"version"`
	GoBinaryName  string `json:"gobinary"`
	PyPackageName string `json:"pypackage"`
}

func (p *Project) Dist() string {
	return fmt.Sprintf("dist/%s-%s.tar.gz", p.PyPackageName, p.Version)
}

func (p *Project) GoBinary() string {
	//TODO: suffix platform
	return fmt.Sprintf("%s", p.GoBinaryName)
}

func (p *Project) MacBinary() string {
	return fmt.Sprintf("%s-mac-%s", p.GoBinaryName, p.Version)
}

func (p *Project) WindowsBinary() string {
	return fmt.Sprintf("%s-win-%s.exe", p.GoBinaryName, p.Version)
}

func (p *Project) LinuxBinary() string {
	return fmt.Sprintf("%s-linux-%s", p.GoBinaryName, p.Version)
}

var ProjectConf *Project

func Config() *Project {

	if ProjectConf != nil {
		return ProjectConf
	}

	jsonData, err := ioutil.ReadFile("config.json")
	if err != nil {
		log.Fatalf("Error reading Json file: %v", err)
	}
	err = json.Unmarshal(jsonData, &ProjectConf)
	if err != nil {
		log.Fatalf("Error parsing YAML: %v", err)
	}

	fmt.Println("pypackage:", ProjectConf.PyPackageName)
	fmt.Println("version:", ProjectConf.Version)
	fmt.Println("gobinary:", ProjectConf.GoBinaryName)
	return ProjectConf
}

// Bootstrap project
func Bootstrap() {
	fmt.Println("Bootstrapping...")
	//TODO: Add the virtualenv creation and pip install scripts here
}

func Settings() {
	Config()
}

func BuildGo() error {

	sh.RunV("pwd")

	c := Config()

	if err := sh.RunV("env", "GOOS=darwin", "go", "build", "-o", c.MacBinary()); err != nil {
		return err
	}

	if err := sh.RunV("env", "GOOS=windows", "go", "build", "-o", c.WindowsBinary()); err != nil {
		return err
	}

	if err := sh.RunV("env", "GOOS=linux", "go", "build", "-o", c.LinuxBinary()); err != nil {
		return err
	}

	if err := sh.RunV("mv", c.MacBinary(), c.PyPackageName); err != nil {
		return err
	}

	if err := sh.RunV("mv", c.WindowsBinary(), c.PyPackageName); err != nil {
		return err
	}

	if err := sh.RunV("mv", c.LinuxBinary(), c.PyPackageName); err != nil {
		return err
	}

	fmt.Println("Go build done!")

	return nil
}

// Build
func Build() error {
	if err := Clean(); err != nil {
		return err
	}
	fmt.Println("Building...")

	BuildGo()

	versionFileContent := fmt.Sprintf("version = '%s'\n", Config().Version)

	file, err := os.OpenFile("iotcore/__version__.py", os.O_WRONLY|os.O_TRUNC, 0644)
	if err != nil {
		fmt.Println("Error opening the file:", err)
		return err
	}
	defer file.Close()

	_, err = file.WriteString(versionFileContent)
	if err != nil {
		fmt.Println("Error writing to the file:", err)
		return err
	}

	if err := sh.RunV("python3", "-m", "build"); err != nil {
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
	if err := sh.Run("pip", "install", Config().Dist()); err != nil {
		return err
	}

	fmt.Println("Package installed!")

	fmt.Println("Run development project..")

	return Run()
}

// Run development django project
func Run() error {
	return sh.RunV("python", "examples/django/manage.py", "runserver")
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

	if err := sh.Run("rm", "-rf", "iotcore.egg-info"); err != nil {
		return err
	}

	if err := sh.Run("rm", "-rf", "iotcore.egg-info"); err != nil {
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
