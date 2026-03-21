[out:json][timeout:30];
area["name:en"="Hong Kong"]->.outer;
(
  nwr["cuisine"~"mexican"](area.outer);
);
out geom;
