[out:json][timeout:30];
area["name:en"="Hong Kong"]->.outer;
(
  nwr["cuisine"~"vietnamese"](area.outer);
);
out geom;
