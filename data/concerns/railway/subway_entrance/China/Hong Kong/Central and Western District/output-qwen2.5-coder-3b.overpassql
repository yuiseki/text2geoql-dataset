[out:json][timeout:30];
area["name:en"="Central and Western District"]->.outer;
(
  nwr["railway"~"subway"](area.outer);
);
out geom;
