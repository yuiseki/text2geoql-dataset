[out:json][timeout:30000];
area["name:en"="Kyoto Prefecture"]->.outer;
area["name:en"="Shimogyo Ward"]->.inner;
(
  nwr["amenity"="place_of_worship"]["religion"="buddhist"](area.inner)(area.outer);
);
out geom;
