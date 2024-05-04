[out:json][timeout:30000];
area["name:en"="Japan"]->.outer;
area["name:en"="Chuo Ward"]->.inner;
(
  nwr["aeroway"="aerodrome"](area.inner)(area.outer);
);
out geom;
