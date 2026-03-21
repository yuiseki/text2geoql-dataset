[out:json][timeout:30];
area["name:en"="Yokohama"]->.outer;
area["name:en"="Kanagawa Prefecture"]->.inner;
(
  nwr["cuisine"~"mexican"](area.inner)(area.outer);
);
out geom;
