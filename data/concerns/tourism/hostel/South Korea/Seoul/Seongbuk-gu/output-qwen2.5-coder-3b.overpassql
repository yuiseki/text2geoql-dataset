[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Seongbuk-gu"]->.inner;
(
  nwr["tourism"="hostel"](area.inner)(area.outer);
);
out geom;
