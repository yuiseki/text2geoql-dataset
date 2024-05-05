[out:json][timeout:30000];
area["name:en"="Fukuoka Prefecture"]->.outer;
area["name:en"="Higashi Ward"]->.inner;
(
  nwr["amenity"="place_of_worship"]["religion"="buddhist"](area.inner)(area.outer);
);
out geom;
