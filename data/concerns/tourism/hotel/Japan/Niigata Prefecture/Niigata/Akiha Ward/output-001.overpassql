[out:json][timeout:30];
area["name:en"="Niigata"]->.outer;
area["name:en"="Akiha Ward"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;
