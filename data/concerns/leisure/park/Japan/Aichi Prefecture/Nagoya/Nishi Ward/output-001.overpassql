[out:json][timeout:30];
area["name:en"="Nagoya"]->.outer;
area["name:en"="Nishi Ward"]->.inner;
(
  nwr["leisure"="park"](area.inner)(area.outer);
);
out geom;
