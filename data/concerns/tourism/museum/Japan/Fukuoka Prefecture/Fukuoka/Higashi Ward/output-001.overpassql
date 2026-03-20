[out:json][timeout:30];
area["name:en"="Fukuoka"]->.outer;
area["name:en"="Higashi Ward"]->.inner;
(
  nwr["tourism"="museum"](area.inner)(area.outer);
);
out geom;
