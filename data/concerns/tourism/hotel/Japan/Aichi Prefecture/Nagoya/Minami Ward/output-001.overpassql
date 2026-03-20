[out:json][timeout:30];
area["name:en"="Nagoya"]->.outer;
area["name:en"="Minami Ward"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;
