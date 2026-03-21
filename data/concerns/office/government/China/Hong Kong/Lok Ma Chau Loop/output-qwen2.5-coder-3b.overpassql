[out:json][timeout:30];
area["name:en"="Hong Kong"]->.outer;
(
  nwr["office"~"government"](area.outer);
);
out geom;
