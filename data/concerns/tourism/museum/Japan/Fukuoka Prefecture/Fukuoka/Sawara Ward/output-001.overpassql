[out:json][timeout:30000];
area["name:en"="Fukuoka"]->.outer;
area["name:en"="Sawara Ward"]->.inner;
(
  nwr["tourism"="museum"](area.inner)(area.outer);
);
out geom;
