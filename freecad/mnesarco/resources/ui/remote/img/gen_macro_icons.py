from pathlib import Path

pattern = 'macro-icon-{}.svg'

colors = [
    '#FCE94F',
    '#8AE234',
    '#FCAF3E',
    '#729FCF',
    '#AD7FA8',
    '#E9B96E',
    '#34E0E2',
    '#FFFFFF',
]

base = 12

root = Path('.')
current = base + 1
for color in colors:
    for i in range(1,base+1):
        source = root.joinpath(pattern.format(i))
        print("Source ", source)
        svg = source.read_text()
        svg2 = svg.replace('fill="#f00"', 'fill="{}"'.format(color))
        root.joinpath(pattern.format(current)).write_text(svg2)
        current += 1