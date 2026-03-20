[out:json][timeout:30];
area["name:en"="Wong Tai Sin District"]->.outer;
(
  nwr["leisure"~"park"](area.outer);
);
out geom;
