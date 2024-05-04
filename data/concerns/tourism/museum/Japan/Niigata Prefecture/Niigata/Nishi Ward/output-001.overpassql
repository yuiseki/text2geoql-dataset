[out:json][timeout:30000];
area["name:en"="Niigata"]->.outer;
area["name:en"="Nishi Ward"]->.inner;
(
  nwr["tourism"="museum"](area.inner)(area.outer);
);
out geom;
