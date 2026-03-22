[out:json][timeout:30];
area["name:en"="Fukuoka Prefecture"]->.outer;
area["name:en"="Fukuoka"]->.inner;
(
  nwr["tourism"="museum"](area.inner)(area.outer);
);
out geom;