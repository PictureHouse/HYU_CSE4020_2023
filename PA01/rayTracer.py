#!/usr/bin/env python3
# -*- coding: utf-8 -*
# sample_python aims to allow seamless integration with lua.
# see examples below

import os
import sys
import pdb  # use pdb.set_trace() for debugging
import code # or use code.interact(local=dict(globals(), **locals()))  for debugging.
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image 

class Color:
    def __init__(self, R, G, B):
        self.color = np.array([R, G, B]).astype(np.float64)

    # Gamma corrects this color.
    # @param gamma the gamma value to use (2.2 is generally used).
    def gammaCorrect(self, gamma):
        inverseGamma = 1.0 / gamma
        self.color = np.power(self.color, inverseGamma)

    def toUINT8(self):
        return (np.clip(self.color, 0, 1) * 255).astype(np.uint8)

class Sphere:
    def __init__(self, shader, center, radius):
        self.shader = shader
        self.center = center
        self.radius = radius

class Camera:
    def __init__(self, viewPoint, viewDir, projNormal, viewUp, projDistance, viewWidth, viewHeight):
        self.viewPoint = viewPoint
        self.viewDir = viewDir
        self.projNormal = projNormal
        self.viewUp = viewUp
        self.projDistance = projDistance
        self.viewWidth = viewWidth
        self.viewHeight = viewHeight

class Light:
    def __init__(self, position, intensity):
        self.position = position
        self.intensity = intensity

class Shader:
    def __init__(self, name, type):
        self.name = name
        self.type = type

class Lambertian(Shader):
    def __init__(self, diffuseColor):
        self.diffuseColor = diffuseColor

class Phong(Shader):
    def __init__(self, diffuseColor, specularColor, exponent):
        self.diffuseColor = diffuseColor
        self.specularColor = specularColor
        self.exponent = exponent

def raytracing(surfaces, ray, viewPoint):
    d = 1e9
    closest = -1
    count = 0

    for i in surfaces:
        if i.__class__.__name__ == 'Sphere':
            a = np.sum(ray * ray)
            b = np.sum((viewPoint - i.center) * ray)
            c = np.sum((viewPoint - i.center) ** 2) - i.radius ** 2
            discriminant = b ** 2 - a * c

            if discriminant >= 0:
                if -b + np.sqrt(discriminant) >= 0:
                    if d >= (-b + np.sqrt(discriminant)) / a:
                        d = (-b + np.sqrt(discriminant)) / a
                        closest = count
                if -b - np.sqrt(discriminant) >= 0:
                    if d >= (-b - np.sqrt(discriminant)) / a:
                        d = (-b - np.sqrt(discriminant)) / a
                        closest = count
        count += 1
    return [d, closest]

def shading(d, closest, ray, viewPoint, surfaces, lights):
    if closest == -1:
        return np.array([0, 0, 0])
    else:
        x = 0
        y = 0
        z = 0
        n = np.array([0, 0, 0])
        v = -d * ray

        if surfaces[closest].__class__.__name__ == 'Sphere':
            n = d * ray + viewPoint  - surfaces[closest].center
            n = n / np.sqrt(np.sum(n * n))

        for i in lights:
            light = v + i.position - viewPoint
            light = light / np.sqrt(np.sum(light * light))
            tmp = raytracing(surfaces, -light, i.position)

            if tmp[1] == closest:
                if surfaces[closest].shader.__class__.__name__ == 'Lambertian':
                    x = x + surfaces[closest].shader.diffuseColor[0] * i.intensity[0] * max(0, np.dot(light, n))
                    y = y + surfaces[closest].shader.diffuseColor[1] * i.intensity[1] * max(0, np.dot(light, n))
                    z = z + surfaces[closest].shader.diffuseColor[2] * i.intensity[2] * max(0, np.dot(light, n)) 
                elif surfaces[closest].shader.__class__.__name__ == 'Phong':
                    v_unit = v / np.sqrt(np.sum(v ** 2))
                    h = v_unit + light
                    h = h / np.sqrt(np.sum(h * h))
                    x = x + surfaces[closest].shader.diffuseColor[0] * max(0, np.dot(n, light)) * i.intensity[0] + surfaces[closest].shader.specularColor[0] * i.intensity[0] * pow(max(0, np.dot(n, h)),surfaces[closest].shader.exponent[0])
                    y = y + surfaces[closest].shader.diffuseColor[1] * max(0, np.dot(n, light)) * i.intensity[1] + surfaces[closest].shader.specularColor[1] * i.intensity[1] * pow(max(0, np.dot(n, h)),surfaces[closest].shader.exponent[0])
                    z = z + surfaces[closest].shader.diffuseColor[2] * max(0, np.dot(n, light)) * i.intensity[2] + surfaces[closest].shader.specularColor[2] * i.intensity[2] * pow(max(0, np.dot(n, h)),surfaces[closest].shader.exponent[0])

        result = Color(x, y, z)
        result.gammaCorrect(2.2)
        return result.toUINT8()

def main():
    tree = ET.parse(sys.argv[1])
    root = tree.getroot()

    # set default values
    viewDir = np.array([0, 0, -1]).astype(np.float64)
    viewUp = np.array([0, 1, 0]).astype(np.float64)
    viewProjNormal = -1 * viewDir  # you can safely assume this. (no examples will use shifted perspective camera)
    viewWidth = 1.0
    viewHeight = 1.0
    projDistance = 1.0
    intensity = np.array([1, 1, 1]).astype(np.float64)  # how bright the light is.
    print(np.cross(viewDir, viewUp))

    # Create an empty image
    imgSize = np.array(root.findtext('image').split()).astype(np.int32)
    channels = 3
    img = np.zeros((imgSize[1], imgSize[0], channels), dtype = np.uint8)
    img[:, :] = 0

    for c in root.findall('camera'):
        viewPoint = np.array(c.findtext('viewPoint').split()).astype(np.float64)
        viewDir = np.array(c.findtext('viewDir').split()).astype(np.float64)
        if c.findtext('projNormal'):
            projNormal = np.array(c.findtext('projNormal').split()).astype(np.float64)
        viewUp = np.array(c.findtext('viewUp').split()).astype(np.float64)
        if c.findtext('projDistance'):
            projDistance = np.array(c.findtext('projDistance').split()).astype(np.float64)
        viewWidth = np.array(c.findtext('viewWidth').split()).astype(np.float64)
        viewHeight = np.array(c.findtext('viewHeight').split()).astype(np.float64)
    camera = Camera(viewPoint, viewDir, projNormal, viewUp, projDistance, viewWidth, viewHeight)

    surfaces = []
    for c in root.findall('surface'):
        if c.get('type') == 'Sphere':
            center = np.array(c.findtext('center').split()).astype(np.float64)
            radius = np.array(c.findtext('radius').split()).astype(np.float64)

            ref = ''
            for check in c:
                if check.tag == 'shader':
                    ref = check.get('ref')

            for d in root.findall('shader'):
                if d.get('name') == ref:
                    if d.get('type') == 'Lambertian':
                        diffuseColor = np.array(d.findtext('diffuseColor').split()).astype(np.float64)
                        shader = Lambertian(diffuseColor)
                        sphere = Sphere(shader, center, radius)
                        surfaces.append(sphere)
                    elif d.get('type') == 'Phong':
                        diffuseColor = np.array(d.findtext('diffuseColor').split()).astype(np.float64)
                        specularColor = np.array(d.findtext('specularColor').split()).astype(np.float64)
                        exponent = np.array(d.findtext('exponent').split()).astype(np.float64)
                        shader = Phong(diffuseColor, specularColor, exponent)
                        sphere = Sphere(shader, center, radius)
                        surfaces.append(sphere)

    lights = []
    for c in root.findall('light'):
        position = np.array(c.findtext('position').split()).astype(np.float64)
        intensity = np.array(c.findtext('intensity').split()).astype(np.float64)
        light = Light(position, intensity)
        lights.append(light)

    x_pixel = camera.viewWidth / imgSize[0]
    y_pixel = camera.viewHeight / imgSize[1]
    w = camera.viewDir
    w_unit = w / np.sqrt(np.sum(w * w))
    u = np.cross(w, camera.viewUp)
    u_unit = u / np.sqrt(np.sum(u * u))
    v = np.cross(w, u)
    v_unit = v / np.sqrt(np.sum(v * v))
    start = w_unit * camera.projDistance - u_unit * x_pixel * ((imgSize[0]/2) + 1/2) - v_unit * y_pixel * ((imgSize[1]/2) + 1/2)

    for y in np.arange(imgSize[0]):
        for x in np.arange(imgSize[1]):
            ray = start + u_unit * x * x_pixel + y_pixel * y * v_unit
            tmp = raytracing(surfaces, ray, camera.viewPoint)
            img[y][x] = shading(tmp[0], tmp[1], ray, camera.viewPoint, surfaces, lights)

    rawimg = Image.fromarray(img, 'RGB')
    rawimg.save(sys.argv[1] + '.png')
    
if __name__ == "__main__":
    main()
