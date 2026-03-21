[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Seongbuk-gu"]->.inner;
(
  nwr["amenity"="community_centre"](area.inner)(area.outer);
);
out geom;
