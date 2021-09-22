import xml.etree.ElementTree as ET


def parseLabelmeXMl(filename: str):
    if filename.endswith('jpg') or filename.endswith('png'):
        filename = filename[:-3] + 'xml'
    try:
        root = ET.parse(filename).getroot()
    except:
        return []

    result = []
    for bbox in root.findall('object'):
        cl = bbox.find('name').text
        bboxVal = [int(bbox.find('bndbox/xmin').text),
                   int(bbox.find('bndbox/ymin').text),
                   int(bbox.find('bndbox/xmax').text),
                   int(bbox.find('bndbox/ymax').text)]
        result.append({"class": cl, "bbox": bboxVal})
    return result
