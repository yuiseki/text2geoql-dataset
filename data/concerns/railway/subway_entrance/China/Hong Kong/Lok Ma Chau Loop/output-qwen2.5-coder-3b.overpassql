[out:json][timeout:30];
area["name:en"="Hong Kong"]->.outer;
(
  nwr["railway"~"subway"](area.outer);
);
out geom;
