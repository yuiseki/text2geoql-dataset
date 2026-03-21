[out:json][timeout:30];
area["name:en"="Kanagawa Prefecture"]->.outer;
area["name:en"="Yokohama"]->.inner;
(
  nwr["sport"="golf"](area.inner)(area.outer);
);
out geom;
