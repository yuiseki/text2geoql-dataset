[out:json][timeout:30];
area["name:en"="Wong Tai Sin District"]->.outer;
(
  nwr["leisure"~"garden"](area.outer);
);
out geom;
