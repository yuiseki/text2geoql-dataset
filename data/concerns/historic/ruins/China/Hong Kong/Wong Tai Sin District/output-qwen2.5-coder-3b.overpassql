[out:json][timeout:30];
area["name:en"="Wong Tai Sin District"]->.outer;
(
  nwr["historic"~"ruin"](area.outer);
);
out geom;
