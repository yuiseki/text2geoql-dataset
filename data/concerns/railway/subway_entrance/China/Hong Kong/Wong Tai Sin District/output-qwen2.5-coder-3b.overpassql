[out:json][timeout:30];
area["name:en"="Wong Tai Sin District"]->.outer;
(
  nwr["railway"~"subway"](area.outer);
);
out geom;
