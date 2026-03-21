[out:json][timeout:30];
area["name:en"="Minami Ward"]->.outer;
area["name:en"="Kanagawa Prefecture"]->.inner;
(
  nwr["leisure"~"dog_park"](area.inner)(area.outer);
);
out geom;
