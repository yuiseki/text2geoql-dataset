[out:json][timeout:30];
area["name:en"="Niigata"]->.outer;
area["name:en"="Chuo Ward"]->.inner;
(
  nwr["leisure"="park"](area.inner)(area.outer);
);
out geom;
