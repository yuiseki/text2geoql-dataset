[out:json][timeout:30];
area["name:en"="Hong Kong"]->.outer;
(
  nwr["railway"~"station"](area.outer);
);
out geom;
