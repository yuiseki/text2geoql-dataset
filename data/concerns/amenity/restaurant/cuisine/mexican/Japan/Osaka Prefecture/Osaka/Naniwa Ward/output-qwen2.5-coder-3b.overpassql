[out:json][timeout:30];
area["name:en"="Osaka"]->.outer;
area["name:en"="Osaka Prefecture"]->.inner;
(
  nwr["cuisine"~"mexican"](area.inner)(area.outer);
);
out geom;
