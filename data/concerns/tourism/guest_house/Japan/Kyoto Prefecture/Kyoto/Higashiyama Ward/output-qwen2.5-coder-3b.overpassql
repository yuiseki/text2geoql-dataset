[out:json][timeout:30];
area["name:en"="Kyoto"]->.outer;
area["name:en"="Higashiyama Ward"]->.inner;
(
  nwr["tourism"="hostel"](area.inner)(area.outer);
);
out geom;
