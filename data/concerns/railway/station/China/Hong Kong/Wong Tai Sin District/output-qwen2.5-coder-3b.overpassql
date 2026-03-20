[out:json][timeout:30];
area["name:en"="Wong Tai Sin District"]->.outer;
(
  nwr["railway"~"station"](area.outer);
);
out geom;
