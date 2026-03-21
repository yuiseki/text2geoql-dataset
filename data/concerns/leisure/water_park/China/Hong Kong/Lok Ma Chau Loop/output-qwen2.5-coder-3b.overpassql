[out:json][timeout:30];
area["name:en"="Hong Kong"]->.outer;
(
  nwr["leisure"~"water_park"](area.outer);
);
out geom;
