[out:json][timeout:30];
area["name:en"="Hong Kong"]->.outer;
(
  nwr["cuisine"~"thai"](area.outer);
);
out geom;
