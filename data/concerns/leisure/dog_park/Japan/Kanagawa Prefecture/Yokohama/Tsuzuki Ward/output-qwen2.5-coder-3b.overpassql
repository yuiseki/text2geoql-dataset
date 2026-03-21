[out:json][timeout:30];
area["name:en"="Yokohama"]->.outer;
area["name:en"="Kanagawa Prefecture"]->.inner;
(
  nwr["leisure"~"dog_park"](area.inner)(area.outer);
);
out geom;
