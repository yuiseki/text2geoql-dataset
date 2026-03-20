[out:json][timeout:30];
area["name:en"="Japan"]->.outer;
area["name:en"="Minami Ward"]->.inner;
(
  nwr["aeroway"="aerodrome"](area.inner)(area.outer);
);
out geom;
