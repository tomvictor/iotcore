//go:build mage
// +build mage

package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"

	"github.com/magefile/mage/sh"
)

const GoBinaryName = "goiotbackend"

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
	return p.GoBinaryName
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
}

func Settings() {
	Config()
}

func BuildGo() error {

	sh.RunV("pwd")

	c := Config()

	if err := sh.RunV("go", "build", "-o", c.GoBinary()); err != nil {
		return err
	}

	if err := sh.RunV("mv", c.GoBinary(), c.PyPackageName); err != nil {
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

	if err := sh.Run("rm", "-rf", "djangoiot.egg-info"); err != nil {
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
