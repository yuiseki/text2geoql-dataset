[out:json][timeout:30];
area["name:en"="Yuen Long District"]->.outer;
(
  nwr["railway"~"subway"](area.outer);
);
out geom;
