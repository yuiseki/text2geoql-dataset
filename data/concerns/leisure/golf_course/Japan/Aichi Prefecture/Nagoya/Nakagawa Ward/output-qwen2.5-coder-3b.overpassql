[out:json][timeout:30];
area["name:en"="Aichi Prefecture"]->.outer;
area["name:en"="Nagoya"]->.inner;
(
  nwr["sport"="golf"](area.inner)(area.outer);
);
out geom;
