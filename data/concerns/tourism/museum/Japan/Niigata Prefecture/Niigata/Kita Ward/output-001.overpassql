[out:json][timeout:30];
area["name:en"="Niigata"]->.outer;
area["name:en"="Kita Ward"]->.inner;
(
  nwr["tourism"="museum"](area.inner)(area.outer);
);
out geom;
