[out:json][timeout:30];
area["name:en"="Wong Tai Sin District"]->.outer;
(
  nwr["leisure"~"playground"](area.outer);
);
out geom;
